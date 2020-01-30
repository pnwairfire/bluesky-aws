import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import getConfig from 'next/config'

import Layout from '../../../../../components/Layout'
import RunOutput from '../../../../../components/RunOutput'

const { publicRuntimeConfig } = getConfig()

export default function Index() {
    const router = useRouter()
    const { request, run } = router.query

    let requestPageUrl = publicRuntimeConfig.basePath
        + '/requests/' + encodeURIComponent(request);

    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/'}>Home</Breadcrumb.Item>
                    <Breadcrumb.Item href={requestPageUrl}>{request}</Breadcrumb.Item>
                    <Breadcrumb.Item active>{run}</Breadcrumb.Item>
                    <Breadcrumb.Item active>Output</Breadcrumb.Item>
                </Breadcrumb>

                <RunOutput request={request} run={run} />

            </div>
        </Layout>
    )
};
