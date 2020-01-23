import { Component } from 'react';
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import Table from 'react-bootstrap/Table'
import Button from 'react-bootstrap/Button'
import Link from 'next/link';


import Layout from '../components/Layout'
import { ApiClient, fetcher } from '../lib/apiutils'
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

    loadRequests(nextIdx) {
        let query = (next) ? ({next}) : ({})

        //let {data, error} = ApiClient.get('api/requests', query);
        ApiClient.getNoSwr('/api/requests/').then(data => {
            let error = null;

            if (data && data.requests) {
                let nextTokens = this.state.nextTokens;
                nextTokens[this.state.nextTokensIdx + 1] = data.next

                this.setState({
                    requests: data && data.requests,
                    previousNext: this.state.currentNext,
                    currentNext: this.state.next,
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
        alert('previous')
        //this.loadRequests();
    };

    handleNextClick = data => {
        alert('next')
        //this.loadRequests();
    };

    render() {
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
                        <Button variant="outline-dark"
                            onClick={this.handlePreviousClick}>&lt;</Button>
                        <Button variant="outline-dark"
                            onClick={this.handleNextClick}>&gt;</Button>
                    </div>
                </div>
            </Layout>
        )
    }
};

export default Index;
