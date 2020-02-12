import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import getConfig from 'next/config'

import Layout from '../../../../../components/Layout'
import RunsTable from '../../../../../components/RunsTable'
import { ApiClient } from '../../../../../lib/apiutils'

const { publicRuntimeConfig } = getConfig()

export default function Index() {
    const router = useRouter();
    const { request, run } = router.query;

    let requestPageUrl = publicRuntimeConfig.basePath
        + '/requests/' + encodeURIComponent(request);

    let {data, fetchError} = {data:null, fetchError:null}
    if (request) {
        let res = ApiClient.get('/api/requests/'
            + encodeURIComponent(request) + '/status');
        data = res.data;
        fetchError = res.fetchError;
    }

    let status = data && data.status;
    let runs = createSingleRunObject(status, run);
    let error = fetchError || (data && data.error);

    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/'}>Home</Breadcrumb.Item>
                    <Breadcrumb.Item href={requestPageUrl}>{request}</Breadcrumb.Item>
                    <Breadcrumb.Item active>{run}</Breadcrumb.Item>
                </Breadcrumb>
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }

                <RunsTable showRunsCount={false} request={request} runs={runs} />
            </div>
        </Layout>
    )
};

function createSingleRunObject(status, run) {
    if (status && status.runs && status.runs[run]) {
        let runs = {}
        runs[run] = status.runs[run]
        return runs
    }
}
