import path from 'path'
import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import getConfig from 'next/config'

import Layout from '../../../../../components/Layout'
import FileViewer from '../../../../../components/FileViewer'

const { publicRuntimeConfig } = getConfig()

export default function Log() {
    const router = useRouter();
    const { request, run } = router.query;

    let requestPageUrl = null;
    let runPageUrl = null;
    let apiPath = null;
    let fileName = "input.json";
    if (request && run) {
        requestPageUrl = publicRuntimeConfig.basePath
            + '/requests/' + encodeURIComponent(request);
        runPageUrl = path.join(requestPageUrl, 'runs', run)
        apiPath = '/api/requests/' + encodeURIComponent(request)
            + '/runs/' + encodeURIComponent(run) + '/input'
    }

    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/'}>Home</Breadcrumb.Item>
                    <Breadcrumb.Item href={requestPageUrl}>{request}</Breadcrumb.Item>
                    <Breadcrumb.Item href={runPageUrl}>{run}</Breadcrumb.Item>
                    <Breadcrumb.Item active>Run Input</Breadcrumb.Item>
                </Breadcrumb>

                <FileViewer apiPath={apiPath} fileName={fileName}
                    header="BlueSky Input" />
            </div>
        </Layout>
    )
};
