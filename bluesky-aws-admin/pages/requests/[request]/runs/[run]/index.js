import path from 'path'
import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import Alert from 'react-bootstrap/Alert'
import Container from 'react-bootstrap/Container'
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import getConfig from 'next/config'

import Layout from '../../../../../components/Layout'
import RunsTable from '../../../../../components/RunsTable'
import FileViewer from '../../../../../components/FileViewer'
import { ApiClient } from '../../../../../lib/apiutils'

const { publicRuntimeConfig } = getConfig()

export default function Index() {
    const router = useRouter();
    const { request, run } = router.query;

    let requestPageUrl = publicRuntimeConfig.basePath
        + '/requests/' + encodeURIComponent(request);

    let {data, fetchError} = {data:null, fetchError:null}
    let inputApiPath = null
    let inputFullPageLink = null
    let configApiPath = null
    let configFullPageLink = null
    if (request && run) {
        let res = ApiClient.get('/api/requests/'
            + encodeURIComponent(request) + '/status');
        data = res.data;
        fetchError = res.fetchError;

        let basePath = path.join('/requests/',
            encodeURIComponent(request), 'runs',
            encodeURIComponent(run));

        inputApiPath = path.join('/api', basePath, 'input')
        inputFullPageLink = {
            hrefPath: "/requests/[request]/runs/[run]/input",
            asPath: path.join(basePath, 'input')
        }

        // run config api path has no run id in it
        configApiPath = path.join('/api/requests/',
            encodeURIComponent(request), '/bluesky-config');
        configFullPageLink = {
            hrefPath: "/requests/[request]/runs/[run]/config",
            asPath: path.join(basePath, 'config')
        }
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

                <Container fluid={true}>
                    <Row>
                        <Col>
                            <RunsTable showRunsCount={false} request={request} runs={runs} />

                        </Col>
                    </Row>
                    <Row>
                        <Col>
                            <FileViewer apiPath={inputApiPath}
                                fullPageLink={inputFullPageLink}
                                header="BlueSky Input" />
                        </Col>
                        <Col>
                            <FileViewer apiPath={configApiPath}
                                fullPageLink={configFullPageLink}
                                header="BlueSky Config" />
                        </Col>
                    </Row>
                    </Container>
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
