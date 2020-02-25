import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import Alert from 'react-bootstrap/Alert'
import Table from 'react-bootstrap/Table'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import getConfig from 'next/config'

import Layout from '../../../components/Layout'
import RequestStatus from '../../../components/RequestStatus';
import RunsTable from '../../../components/RunsTable';
import FileViewer from '../../../components/FileViewer'
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
    let inputApiPath = null
    let inputFullPageLink = null
    let configApiPath = null
    let configFullPageLink = null
    if (request) {
        let res = ApiClient.get('/api/requests/'
            + encodeURIComponent(request) + '/status');
        data = res.data;
        fetchError = res.fetchError;
        inputApiPath = '/api/requests/' + encodeURIComponent(request) + '/input';
        inputFullPageLink = {
            hrefPath: "/requests/[request]/input",
            asPath: `/requests/${encodeURIComponent(request)}/input`
        }
        configApiPath = '/api/requests/'
            + encodeURIComponent(request) + '/bluesky-aws-config';

        configFullPageLink = {
            hrefPath: "/requests/[request]/config",
            asPath: `/requests/${encodeURIComponent(request)}/config`
        }
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

                <Container fluid={true}>
                    <Row>
                        <Col>
                            <RequestStatus request={request} status={status} />
                        </Col>
                    </Row>
                    <Row>
                        <Col>
                            <RunsTable showRunsCount={true} request={request} runs={runs} />
                        </Col>
                    </Row>
                    <Row>
                        <Col>
                            <FileViewer apiPath={inputApiPath}
                                fullPageLink={inputFullPageLink}
                                header="Request Input" />
                        </Col>
                        <Col>
                            <FileViewer apiPath={configApiPath}
                                fullPageLink={configFullPageLink}
                                header="Request Config" />
                        </Col>
                    </Row>
                    </Container>
            </div>
        </Layout>
    )
};