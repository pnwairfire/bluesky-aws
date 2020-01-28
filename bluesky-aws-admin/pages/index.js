import { Component } from 'react';
import Breadcrumb from 'react-bootstrap/Breadcrumb'

import Layout from '../components/Layout'
import RequestsTable from '../components/RequestsTable'
import { ApiClient, fetcher } from '../lib/apiutils'
import styles from './index.module.css'


//const Index = props => {
//    let requests = props.requests;
//    let error = props.error
export default class Index extends Component {

    constructor(props) {
        super(props);

        this.state = {
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
        let query = (nextTokensIdx && this.state.nextTokens[nextTokensIdx])
            ? ({next: this.state.nextTokens[nextTokensIdx]}) : ({})

        console.log('query: ' + JSON.stringify(query));

        this.setState({
            loading: true
        }, () => {
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
        console.log(prevDisabled + '/' +nextDisabled);
        return (
            <Layout>
                <Breadcrumb>
                    <Breadcrumb.Item active>Home</Breadcrumb.Item>
                </Breadcrumb>
                <RequestsTable
                    loading={this.state.loading}
                    requests={this.state.requests}
                    error={this.state.error}
                    handleNextClick={this.handleNextClick}
                    handlePreviousClick={this.handlePreviousClick}
                    handleReloadClick={this.handleReloadClick}
                    nextDisabled={nextDisabled}
                    prevDisabled={prevDisabled}
                    reloadDisabled={this.loading} />
            </Layout>
        )
    }
};
