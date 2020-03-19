import Alert from 'react-bootstrap/Alert'
import Table from 'react-bootstrap/Table'

import LoadingSpinner from './LoadingSpinner';
import Link from '../components/Link';

export default function RequestsTable(props) {
    return (
        <div>
            {props.error &&
                <Alert variant="danger">
                    {props.error}
                </Alert>
            }
            <h4>{props.headerPrefix || ''} Requests {props.requests && '('+props.requests.length+')'}</h4>
            {props.loading && (
                <LoadingSpinner />
            ) || (
                <div>
                    <Table striped bordered hover>
                        <thead>
                            <tr>
                                <th>Request Id</th>
                                <th>Last Modified</th>
                            </tr>
                          </thead>
                        <tbody>
                            {props.requests && props.requests.map((request, idx) => (
                                <tr key={idx}>

                                    <td>
                                        <Link href="/requests/[id]"
                                                as={`/requests/${encodeURIComponent(request.requestId)}`}>
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
                </div>
            )}
        </div>
    )
}