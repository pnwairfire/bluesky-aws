import Table from 'react-bootstrap/Table'
import Link from 'next/link';

import Layout from '../components/Layout'
import { ApiClient } from '../lib/apiutils'



//const Index = props => {
//    let requests = props.requests;
//    let error = props.error
function Index() {
    let {data, fetchError} = ApiClient.get('api/requests');

    let requests = data && data.requests;
    let error = fetchError || (data && data.error);

    return (
        <Layout>
            <div>
                {error &&
                    <Alert variant="danger">
                        error
                    </Alert>
                }
                <h4>Requests {requests && '('+requests.length+')'}</h4>
                <Table striped bordered hover>
                    <thead>
                        <tr>
                            <th>Request Id</th>
                            <th>Last Modified</th>
                        </tr>
                      </thead>
                    <tbody>
                        {requests && requests.map((request, idx) => (
                            <tr key={idx}>

                                <td>
                                    <Link href="/requests/[id]" as={`/requests/${request.requestId}`}>
                                        <a>{request.requestId} </a>
                                    </Link>
                                </td>
                                    {request.ts}
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </div>
        </Layout>
    )
};

export default Index;
