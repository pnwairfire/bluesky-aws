import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import getConfig from 'next/config'

import Layout from '../../../components/Layout'
import FileViewer from '../../../components/FileViewer'

const { publicRuntimeConfig } = getConfig()

//const Index = props => {
//    let requests = props.requests;
//    let error = props.error
export default function Index() {
    const router = useRouter()
    const { request } = router.query


    let requestPageUrl = null;
    let apiPath = null
    if (request) {
        requestPageUrl = publicRuntimeConfig.basePath
            + '/requests/' + encodeURIComponent(request);
        apiPath = '/api/requests/' + encodeURIComponent(request) + '/input';
    }
    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/'}>Home</Breadcrumb.Item>
                    <Breadcrumb.Item href={requestPageUrl}>{request}</Breadcrumb.Item>
                    <Breadcrumb.Item active>Input</Breadcrumb.Item>

                </Breadcrumb>
                <FileViewer apiPath={apiPath} header="Request Input" />
            </div>
        </Layout>
    )
};