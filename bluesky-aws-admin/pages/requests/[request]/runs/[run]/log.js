import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import Alert from 'react-bootstrap/Table'
import getConfig from 'next/config'

import Layout from '../../../../../components/Layout'
import RunLog from '../../../../../components/RunLog'
import { getRunLog } from '../../../../../lib/status'
import { ApiClient } from '../../../../../lib/apiutils'

const { publicRuntimeConfig } = getConfig()

export default function Index() {
    const router = useRouter()
    const { request, run } = router.query


    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/'}>Home</Breadcrumb.Item>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/requests/'+ request}>{request}</Breadcrumb.Item>
                    <Breadcrumb.Item active>{run}</Breadcrumb.Item>
                    <Breadcrumb.Item active>Log</Breadcrumb.Item>
                </Breadcrumb>

                <RunLog request={request} run={run} />

            </div>
        </Layout>
    )
};
