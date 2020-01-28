import Alert from 'react-bootstrap/Alert'
import Table from 'react-bootstrap/Table'
import Button from 'react-bootstrap/Button'
import Spinner from 'react-bootstrap/Spinner'

import Link from '../components/Link';
import styles from './RequestsTable.module.css'

export default function RequestsTable(props) {
    return (
        <div>
            {props.error &&
                <Alert variant="danger">
                    {props.error}
                </Alert>
            }
            <h4>Requests {props.requests && '('+props.requests.length+')'}</h4>
            {props.loading && (
                <div className={styles['loading-spinner']}>
                    <Spinner animation="border" role="status" size="sm">
                    </Spinner>
                    <span>Loading...</span>
                </div>
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
                            onClick={props.handlePreviousClick}
                            disabled={props.prevDisabled}>&lt;</Button>
                        <Button variant="outline-dark" size="sm"
                            onClick={props.handleNextClick}
                            disabled={props.nextDisabled}>&gt;</Button>
                    </div>
                </div>
            )}
        </div>
    )
}