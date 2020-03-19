import { useRouter } from 'next/router'
import { useState, Component } from 'react';
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import Button from 'react-bootstrap/Button'
import Modal from 'react-bootstrap/Modal'
import Calendar from 'react-calendar';
import strftime from 'strftime'
import {
    FaAngleRight, FaAngleLeft, FaSyncAlt, FaRegCalendarAlt
} from "react-icons/fa";

import Layout from '../components/Layout'
import RequestsTable from '../components/RequestsTable'
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

    handleReloadClick = data => {
        this.loadRequests(this.state.nextTokensIdx);
    };

    render() {
        let prevDisabled = this.state.nextTokensIdx <= 0;
        let nextDisabled = ! this.state.nextTokens[this.state.nextTokensIdx + 1]
        //console.log(prevDisabled + '/' +nextDisabled);
        return (
            <Layout>
                <Breadcrumb>
                    <Breadcrumb.Item active>Home</Breadcrumb.Item>
                </Breadcrumb>
                <div className={styles['pagination-controls']}>
                    <CalendarModal
                        month={this.state.month}
                        handleMonthChange={this.handleMonthChange} />
                    <Button variant="outline-dark" size="sm"
                        onClick={this.handleReloadClick}
                        disabled={this.state.loading}>
                        <FaSyncAlt />
                    </Button>
                    <Button variant="outline-dark" size="sm"
                        onClick={this.handlePreviousClick}
                        disabled={prevDisabled}>
                        <FaAngleLeft />
                    </Button>
                    <Button variant="outline-dark" size="sm"
                        onClick={this.handleNextClick}
                        disabled={nextDisabled}>
                        <FaAngleRight />
                    </Button>
                </div>
                <RequestsTable
                    headerPrefix={strftime('%B %Y', this.state.month)}
                    loading={this.state.loading}
                    requests={this.state.requests}
                    error={this.state.error} />
            </Layout>
        )
    }
};


function CalendarModal(props) {
    const [show, setShow] = useState(false);

    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);
    const onChange = (date) => {
        props.handleMonthChange(date)
        setShow(false);
    }

    return (
        <>
          <Button variant="outline-dark" size="sm" onClick={handleShow}>
            <FaRegCalendarAlt />
          </Button>

          <Modal show={show} onHide={handleClose}
                animation={false} centered>
            <Modal.Body>
                <Calendar
                    defaultView="year"
                    onChange={onChange}
                    value={props.month}
                    maxDetail="year"
                    minDetail="year"
                />
            </Modal.Body>
          </Modal>
        </>
    );
}
