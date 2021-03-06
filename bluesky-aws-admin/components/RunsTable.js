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
        // Note that the links to the log and output *pages* will only
        // be displayed if log_url and output_url, respectively, are defined,
        // even though it's not the urls are not directly used on this page.
        // The python code that sets the log and output urls only does so
        // after checking s3 for the existence of the keys.
        return (
            <WrappedRunsTable numRuns={props.showRunsCount && Object.entries(props.runs).length}>
                <Table bordered hover>
                    <thead>
                        <tr>
                            <th>Run Id</th>
                            <th>Location</th>
                            <th>Area</th>
                            <th>Status</th>
                            <th>Config</th>
                            <th>Input</th>
                            <th>Log File</th>
                            <th>Output</th>
                        </tr>
                    </thead>
                    <tbody>
                        {Object.keys(props.runs).map((runId, idx) => (
                            <RunRow request={props.request}
                                idx={idx} runId={runId}
                                run={props.runs[runId]}
                                linkToRunPage={props.linkToRunPage} />
                        ))}
                    </tbody>
                </Table>
            </WrappedRunsTable>
        )
    }
}

function WrappedRunsTable(props) {
    return (
        <div className={styles['runs-table']}>
            <h5>{props.numRuns || ''} Runs</h5>
            {props.children}
        </div>
    )
}


function RunRow(props) {
    let outputHrefUrlObj = {
        pathname: "/requests/[request]/runs/[run]/output-files/view",
        query: {name: 'output.json'}
    }
    let outputAsUrlObj = {
        pathname: `/requests/${encodeURIComponent(props.request)}/runs/${encodeURIComponent(props.runId)}/output-files/view`,
        query: {name: 'output.json'}
    }

    return (
        <tr key={props.idx} className={styles[props.run.status]}>
            <td>
                {props.linkToRunPage && (
                    <Link href="/requests/[request]/runs/[run]"
                            as={`/requests/${encodeURIComponent(props.request)}/runs/${encodeURIComponent(props.runId)}`}>
                        <a>{props.runId}</a>
                    </Link>
                ) || (
                    <span>{props.runId}</span>
                )}
            </td>
            <td>
                {props.run.fire_info && props.run.fire_info.lat && (
                    <span>{props.run.fire_info.lat}, {props.run.fire_info.lng}</span>
                ) || (
                    <span>?</span>
                )}
            </td>
            <td>
                {props.run.fire_info && props.run.fire_info.area != null && (
                    <span>{props.run.fire_info.area} acres</span>
                ) || (
                    <span>?</span>
                )}
            </td>
            <td className={styles['status-cell']}>
                <span>{props.run.status}</span>
            </td>
            <td>
                <Link href="/requests/[request]/runs/[run]/config"
                        as={`/requests/${encodeURIComponent(props.request)}/runs/${encodeURIComponent(props.runId)}/config`}>
                    <a>config</a>
                </Link>
            </td>
            <td>
                <Link href="/requests/[request]/runs/[run]/input"
                        as={`/requests/${encodeURIComponent(props.request)}/runs/${encodeURIComponent(props.runId)}/input`}>
                    <a>input</a>
                </Link>
            </td>
            <td>
                {props.run.log_url && (
                    <Link href="/requests/[request]/runs/[run]/log"
                            as={`/requests/${encodeURIComponent(props.request)}/runs/${encodeURIComponent(props.runId)}/log`}>
                        <a>log</a>
                    </Link>
                ) || (
                    <div><i>(n/a)</i></div>
                )}
            </td>
            <td className={styles['run-output']}>
                {props.run.output_url && (
                    <div>
                        <Link href={outputHrefUrlObj} as={outputAsUrlObj}>
                            <a>output</a>
                        </Link>
                        /
                        <Link href="/requests/[request]/runs/[run]/output-files"
                                as={`/requests/${encodeURIComponent(props.request)}/runs/${encodeURIComponent(props.runId)}/output-files`}>
                            <a>output files</a>
                        </Link>
                    </div>
                ) || (
                    <div><i>(n/a)</i></div>
                )}
            </td>
        </tr>
    )
}
