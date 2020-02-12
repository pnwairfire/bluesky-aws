import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import Alert from 'react-bootstrap/Alert'
import Table from 'react-bootstrap/Table'
import getConfig from 'next/config'

import Layout from '../../../components/Layout'
import RequestStatus from '../../../components/RequestStatus';
import RunsTable from '../../../components/RunsTable';
import RequestInput from '../../../components/RequestInput';
import { ApiClient } from '../../../lib/apiutils'

import styles from './index.module.css'

const { publicRuntimeConfig } = getConfig()

//const Index = props => {
//    let requests = props.requests;
//    let error = props.error
export default function Index() {
    const router = useRouter()
    const { request } = router.query

    let {data, fetchError} = {data:null, fetchError:null}
    if (request) {
        let res = ApiClient.get('/api/requests/'
            + encodeURIComponent(request) + '/status');
        data = res.data;
        fetchError = res.fetchError;
    }

    let status = data && data.status;
    let runs = status && status.runs;
    let error = fetchError || (data && data.error);

    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/'}>Home</Breadcrumb.Item>
                    {request &&
                        <Breadcrumb.Item active>{request}</Breadcrumb.Item>
                    }
                </Breadcrumb>
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }

                <RequestStatus request={request} status={status} />
                <RunsTable showRunsCount={true} request={request} runs={runs} />
                <RequestInput request={request} />
            </div>
        </Layout>
    )
};