//import { useRouter } from 'next/router'
import { Component } from 'react';
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import Button from 'react-bootstrap/Button'
import strftime from 'strftime'
import {
    FaAngleRight, FaAngleLeft, FaAngleDoubleRight, FaAngleDoubleLeft,
    FaSyncAlt
} from "react-icons/fa";

import Layout from '../components/Layout'
import RequestsTable from '../components/RequestsTable'
import CalendarModal from '../components/CalendarModal'
import ButtonWithToolTip from '../components/ButtonWithToolTip'
import { ApiClient, fetcher } from '../lib/apiutils'
import styles from './index.module.css'


// TODO: To support deep linking to a specific month, we could use
//    A query param, such as '?month=202003'.  We could use 'useRouter'
//    access the query string, but that would requred wrapping the
//    class component 'Page' in function component - something like
//    following
// export default function Index() {
//     let today = new Date();
//     const router = useRouter()
//     const { month } = router.query
//     let monthObj = moment(month, "YYYYMM")

//     // console.log(month)

//     return (
//         <Page month={monthObj} />
//     )
// }

export default class Page extends Component {

    constructor(props) {
        super(props);

        this.state = {
            month: props.month || new Date(),
            requests: [],
            error: null,
            // continuation tokens for previous set, this set, and next
            nextTokens: [null],
            nextTokensIdx: 0,
            loading: true
        };
        // this.handlePreviousClick = this.handlePreviousClick.bind(this)
        // this.handleNextClick = this.handleNextClick.bind(this)
    }


    loadRequests(nextTokensIdx) {
        nextTokensIdx = nextTokensIdx || 0;
        let query = {
            datePrefix: strftime('%Y%m', this.state.month)
        }
        if (nextTokensIdx && this.state.nextTokens[nextTokensIdx]) {
            query.next = this.state.nextTokens[nextTokensIdx]
        }

        console.log('query: ' + JSON.stringify(query));

        this.setState({loading: true}, () => {
            //let {data, error} = ApiClient.get('api/requests', query);
            ApiClient.getNoSwr('/api/requests/', query).then((data) => {
                let error = null;
                if (data && data.requests) {
                    let nextTokens = this.state.nextTokens;
                    nextTokens[nextTokensIdx + 1] = data.next

                    this.setState({
                        requests: data && data.requests,
                        nextTokens: nextTokens,
                        nextTokensIdx: nextTokensIdx,
                        next: data && data.next,
                        error: error || (data && data.error),
                        loading: false
                    })
                } else {
                    this.setState({
                        error:"Failed to load requests",
                        loading: false
                    })
                }
            }).catch(error => {
                    this.setState({
                        error:"Failed to load requests",
                        loading: false
                    })
            })
        })
    }

    componentDidMount() {
        this.loadRequests();
    }

    handleMonthChange = date => {
        console.log("selected date: " + date);
        this.setState({
            month: date,
            nextTokens: [null],
            nextTokensIdx: 0
        }, () => {
            this.loadRequests(this.state.nextTokensIdx);
        })
    }

    handlePreviousClick = data => {
        this.loadRequests(this.state.nextTokensIdx - 1);
    };

    handleNextClick = data => {
        this.loadRequests(this.state.nextTokensIdx + 1);
    };

    handleFirstClick = data => {
        this.loadRequests(0);
    };

    handlePageClick = idx => {
        this.loadRequests(idx);
    };

    // Pagination uses continuation tokens, so the last page can't be
    // jumped to directly.  Starting from the furthest page whose token is
    // known, follow the tokens until a page has no 'next'.
    handleLastClick = async data => {
        let nextTokens = this.state.nextTokens;
        let idx = 0;
        while (nextTokens[idx + 1]) {
            idx++;
        }

        this.setState({loading: true});
        try {
            let resp;
            while (true) {
                let query = {datePrefix: strftime('%Y%m', this.state.month)};
                if (idx && nextTokens[idx]) {
                    query.next = nextTokens[idx];
                }
                resp = await ApiClient.getNoSwr('/api/requests/', query);
                if (!resp || !resp.requests) {
                    throw new Error("Failed to load requests");
                }
                nextTokens[idx + 1] = resp.next;
                if (!resp.next) {
                    break;
                }
                idx++;
            }
            this.setState({
                requests: resp.requests,
                nextTokens: nextTokens,
                nextTokensIdx: idx,
                next: resp.next,
                error: resp.error,
                loading: false
            });
        } catch (error) {
            this.setState({
                error: "Failed to load requests",
                loading: false
            });
        }
    };

    handleReloadClick = data => {
        this.loadRequests(this.state.nextTokensIdx);
    };

    renderPagination() {
        let idx = this.state.nextTokensIdx;
        let prevDisabled = idx <= 0;
        let nextDisabled = ! this.state.nextTokens[idx + 1];
        let variant = disabled => (disabled ? 'light' : 'primary');

        // numbered buttons for the current page and the ones before and
        // after it (pages are displayed 1-based)
        let pageIdxs = [idx - 1, idx, idx + 1].filter(i =>
            i >= 0 && (i <= idx || this.state.nextTokens[i]));

        return (
            <div className={styles['pagination-controls']}>
                <ButtonWithToolTip
                    title="Load First"
                    variant={variant(prevDisabled)}
                    onClick={this.handleFirstClick}
                    disabled={prevDisabled || this.state.loading}>
                    <FaAngleDoubleLeft />
                </ButtonWithToolTip>
                <ButtonWithToolTip
                    title="Load Previous"
                    variant={variant(prevDisabled)}
                    onClick={this.handlePreviousClick}
                    disabled={prevDisabled || this.state.loading}>
                    <FaAngleLeft />
                </ButtonWithToolTip>
                {pageIdxs.map(i => (
                    <ButtonWithToolTip
                        key={i}
                        title={"Page " + (i + 1)}
                        variant={(i === idx) ? 'primary' : 'outline-primary'}
                        onClick={() => this.handlePageClick(i)}
                        disabled={i === idx || this.state.loading}>
                        {i + 1}
                    </ButtonWithToolTip>
                ))}
                <ButtonWithToolTip
                    title="Load Next"
                    variant={variant(nextDisabled)}
                    onClick={this.handleNextClick}
                    disabled={nextDisabled || this.state.loading}>
                    <FaAngleRight />
                </ButtonWithToolTip>
                <ButtonWithToolTip
                    title="Load Last"
                    variant={variant(nextDisabled)}
                    onClick={this.handleLastClick}
                    disabled={nextDisabled || this.state.loading}>
                    <FaAngleDoubleRight />
                </ButtonWithToolTip>
            </div>
        )
    }

    render() {
        let prevDisabled = this.state.nextTokensIdx <= 0;
        let nextDisabled = ! this.state.nextTokens[this.state.nextTokensIdx + 1]
        let showPaginationButtons = !prevDisabled || !nextDisabled;
        return (
            <Layout>
                <Breadcrumb>
                    <Breadcrumb.Item active>Home</Breadcrumb.Item>
                </Breadcrumb>
                <div className={styles['controls-row']}>
                    <div className={styles['pagination-controls']}>
                        <CalendarModal
                            variant="primary"
                            month={this.state.month}
                            handleMonthChange={this.handleMonthChange} />
                        <ButtonWithToolTip
                            title="Reload"
                            variant="primary"
                            onClick={this.handleReloadClick}
                            disabled={this.state.loading}>
                            <FaSyncAlt />
                        </ButtonWithToolTip>
                    </div>
                    {showPaginationButtons && this.renderPagination()}
                </div>
                <RequestsTable
                    headerPrefix={strftime('%B %Y', this.state.month)}
                    loading={this.state.loading}
                    requests={this.state.requests}
                    error={this.state.error} />
                {showPaginationButtons && (
                    <div className={styles['controls-row']}>
                        {this.renderPagination()}
                    </div>
                )}
            </Layout>
        )
    }
};
