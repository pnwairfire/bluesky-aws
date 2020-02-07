import path from 'path'
import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import getConfig from 'next/config'

import Layout from '../../../../../../components/Layout'
import RunOutputFiles from '../../../../../../components/RunOutputFiles'

const { publicRuntimeConfig } = getConfig()

export default function Index() {
    const router = useRouter()
    const { request, run } = router.query

    let requestPageUrl = null;
    let runPageUrl = null;
    if (request && run) {
        requestPageUrl = publicRuntimeConfig.basePath
            + '/requests/' + encodeURIComponent(request);
        runPageUrl = path.join(requestPageUrl, 'runs', run)
    }

    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/'}>Home</Breadcrumb.Item>
                    <Breadcrumb.Item href={requestPageUrl}>{request}</Breadcrumb.Item>
                    <Breadcrumb.Item href={runPageUrl}>{run}</Breadcrumb.Item>
                    <Breadcrumb.Item active>Output Files</Breadcrumb.Item>
                </Breadcrumb>

                <RunOutputFiles request={request} run={run} />
            </div>
        </Layout>
    )
};
