import path from 'path'
import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import getConfig from 'next/config'

import Layout from '../../../../../../components/Layout'
import FileViewer from '../../../../../../components/FileViewer'

const { publicRuntimeConfig } = getConfig()

export default function Index() {
    const router = useRouter();
    const { request, run, name } = router.query;

    let requestPageUrl = null;
    let outputFilesPageUrl = null;
    if (request && run && name) {
        requestPageUrl = publicRuntimeConfig.basePath
            + '/requests/' + encodeURIComponent(request);

        outputFilesPageUrl = path.join(requestPageUrl,
            'runs', run, 'output-files')
    }
    // else it's not the final rendering, so just leave urls as null

    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/'}>Home</Breadcrumb.Item>
                    <Breadcrumb.Item href={requestPageUrl}>{request}</Breadcrumb.Item>
                    <Breadcrumb.Item active>{run}</Breadcrumb.Item>
                    <Breadcrumb.Item href={outputFilesPageUrl}>Output Files</Breadcrumb.Item>
                    <Breadcrumb.Item active>{name}</Breadcrumb.Item>
                </Breadcrumb>

                <FileViewer request={request} run={run} name={name} />
            </div>
        </Layout>
    )
};
