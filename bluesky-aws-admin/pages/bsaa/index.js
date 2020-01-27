import { Component } from 'react';
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import Alert from 'react-bootstrap/Alert'
import Table from 'react-bootstrap/Table'
import Button from 'react-bootstrap/Button'

import Link from '../../components/Link';
import Layout from '../../components/Layout'
import { ApiClient, fetcher } from '../../lib/apiutils'
//import $ from 'jquery';




//const Index = props => {
//    let requests = props.requests;
//    let error = props.error
export class Index extends Component {

    constructor(props) {
        super(props);

        this.state = {
            requests: [],
            error: null,
            // continuation tokens for previous set, this set, and next
            nextTokens: [null],
            nextTokensIdx: 0
        };
        // this.handlePreviousClick = this.handlePreviousClick.bind(this)
        // this.handleNextClick = this.handleNextClick.bind(this)
    }

    loadRequests(nextTokensIdx) {
        nextTokensIdx = nextTokensIdx || 0;
        let query = (nextTokensIdx && this.state.nextTokens[nextTokensIdx])
            ? ({next: this.state.nextTokens[nextTokensIdx]}) : ({})

        console.log('query: ' + JSON.stringify(query));

        //let {data, error} = ApiClient.get('bsaa/api/requests', query);
        ApiClient.getNoSwr('/bsaa/api/requests/', query).then((data) => {
            let error = null;
            if (data && data.requests) {
                let nextTokens = this.state.nextTokens;
                nextTokens[nextTokensIdx + 1] = data.next


                this.setState({
                    requests: data && data.requests,
                    nextTokens: nextTokens,
                    nextTokensIdx: nextTokensIdx,
                    next: data && data.next,
                    error: error || (data && data.error)
                })
            } else {
                this.setState({
                    error:"Failed to load requests"
                })
            }
        }).catch(error => {
                this.setState({
                    error:"Failed to load requests"
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

    render() {
        let prevDisabled = this.state.nextTokensIdx <= 0;
        let nextDisabled = ! this.state.nextTokens[this.state.nextTokensIdx + 1]
        console.log(prevDisabled + '/' +nextDisabled);
        return (
            <Layout>
                <div>
                    <Breadcrumb>
                        <Breadcrumb.Item active>Home</Breadcrumb.Item>
                    </Breadcrumb>
                    {this.state.error &&
                        <Alert variant="danger">
                            {this.state.error}
                        </Alert>
                    }
                    <h4>Requests {this.state.requests && '('+this.state.requests.length+')'}</h4>
                    <Table striped bordered hover>
                        <thead>
                            <tr>
                                <th>Request Id</th>
                                <th>Last Modified</th>
                            </tr>
                          </thead>
                        <tbody>
                            {this.state.requests && this.state.requests.map((request, idx) => (
                                <tr key={idx}>

                                    <td>
                                        <Link href="/requests/[id]"
                                                as={`/requests/${request.requestId}`}>
                                            <a>{request.requestId} </a>
                                        </Link>
                                    </td>
                                    <td>
                                        {request.ts}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                    <div>
                        <Button variant="outline-dark" size="sm"
                            onClick={this.handlePreviousClick}
                            disabled={prevDisabled}>&lt;</Button>
                        <Button variant="outline-dark" size="sm"
                            onClick={this.handleNextClick}
                            disabled={nextDisabled}>&gt;</Button>
                    </div>
                </div>
            </Layout>
        )
    }
};

export default Index;
