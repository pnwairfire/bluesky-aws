import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import Alert from 'react-bootstrap/Table'
import Table from 'react-bootstrap/Table'
import getConfig from 'next/config'

import Link from '../../../components/Link';
import Layout from '../../../components/Layout'
import RequestInput from '../../../components/RequestInput';
import { ApiClient } from '../../../lib/apiutils'

const { publicRuntimeConfig } = getConfig()


//const Index = props => {
//    let requests = props.requests;
//    let error = props.error
export default function Index() {
    const router = useRouter()
    const { request } = router.query

    let {data, fetchError} = {data:null, fetchError:null}
    if (request) {
        let res = ApiClient.get('/api/requests/' + request + '/status');
        data = res.data;
        fetchError = res.fetchError;
    }

    let status = data && data.status;
    let error = fetchError || (data && data.error);

    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/'}>Home</Breadcrumb.Item>
                    <Breadcrumb.Item active>{request}</Breadcrumb.Item>
                </Breadcrumb>
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }

                <RequestBlock request={request} status={status} />
                <RequestInput request={request} />
            </div>
        </Layout>
    )
};

function RequestBlock(props) {
    if (props && props.status){
        return (
            <div className="request">
                <div><b>Request</b>: {props.request}</div>
                <div><b>System</b>: {props.status.system_state}</div>
                {props.status.system_error &&
                    <div><b>Error</b>: {props.status.system_error}</div>
                }
                <div><b>Message</b>: {props.status.system_message || '(none)'}</div>
                <RunsTable request={props.request} runs={props.status.runs} />

            </div>
        )
    } else {
        return <div><i>(no request status information)</i></div>
    }
}

function RunsTable(props) {
    if (props.runs) {
        return (
            <div>
                <hr />
                <h5>Runs</h5>
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
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }

}
