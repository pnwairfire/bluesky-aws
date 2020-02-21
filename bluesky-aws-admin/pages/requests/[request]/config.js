import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import getConfig from 'next/config'

import Layout from '../../../components/Layout'
import ConfigViewer from '../../../components/ConfigViewer';

const { publicRuntimeConfig } = getConfig()

//const Index = props => {
//    let requests = props.requests;
//    let error = props.error
export default function Index() {
    const router = useRouter()
    const { request } = router.query


    let requestPageUrl = null;
    if (request) {
        requestPageUrl = publicRuntimeConfig.basePath
            + '/requests/' + encodeURIComponent(request);
    }
    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href={publicRuntimeConfig.basePath + '/'}>Home</Breadcrumb.Item>
                    <Breadcrumb.Item href={requestPageUrl}>{request}</Breadcrumb.Item>
                    <Breadcrumb.Item active>Request Config</Breadcrumb.Item>

                </Breadcrumb>
                <ConfigViewer request={request} />
            </div>
        </Layout>
    )
};