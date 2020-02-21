import path from 'path'
import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import getConfig from 'next/config'

import Layout from '../../../../../components/Layout'
import ConfigViewer from '../../../../../components/ConfigViewer';

const { publicRuntimeConfig } = getConfig()

export default function Log() {
    const router = useRouter();
    const { request, run } = router.query;

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
                    <Breadcrumb.Item active>Run Config</Breadcrumb.Item>
                </Breadcrumb>

                <ConfigViewer showRunConfig={true} request={request} />
            </div>
        </Layout>
    )
};
