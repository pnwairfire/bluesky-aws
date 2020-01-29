import Table from 'react-bootstrap/Table'
import Alert from 'react-bootstrap/Alert'

import LoadingSpinner from './LoadingSpinner';
import Link from './Link';
import styles from './RunsTable.module.css'

export default function RunsTable(props) {
    if (!props.runs) {
        return (
            <WrappedRunsTable>
                <LoadingSpinner />
            </WrappedRunsTable>
        )
    } else if (Object.entries(props.runs).length === 0) {
        return (
            <WrappedRunsTable>
                <Alert variant="warning">
                    (No runs in progress or completed)
                </Alert>
            </WrappedRunsTable>
        )
    } else {
        return (
            <WrappedRunsTable>
                <Table striped bordered hover>
                    <thead>
                        <tr>
                            <th>Run Id</th>
                            <th>Status</th>
                            <th>Log File</th>
                            <th>Output</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Object.keys(props.runs).map((runId, idx) => (
                            <tr key={idx}>
                                <td>{runId}</td>
                                <td>{props.runs[runId].status}</td>
                                <td>
                                    <Link href="/requests/[request]/runs/[run]/log"
                                            as={`/requests/${props.request}/runs/${runId}/log`}>
                                        <a>log</a>
                                    </Link>
                                </td>
                                <td>
                                    <a target="_blank" href={props.runs[runId].output_url}>Output</a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </WrappedRunsTable>
        )
    }
}

function WrappedRunsTable(props){
    return (
        <div className={styles['runs-table']}>
            <h5>Runs</h5>
            {props.children}
        </div>
    )
}