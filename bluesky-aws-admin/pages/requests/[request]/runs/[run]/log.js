import { useRouter } from 'next/router'
import Breadcrumb from 'react-bootstrap/Breadcrumb'
import Alert from 'react-bootstrap/Table'

import Layout from '../../../../../components/Layout'
import { getRunLog } from '../../../../../lib/status'
import { ApiClient } from '../../../../../lib/apiutils'

import styles from './log.module.css'

export default function Index() {
    const router = useRouter()
    const { request, run } = router.query
    console.log(request + ' - ' + run)

    let path ='/api/requests/' + request + '/runs/' + run + '/log'
    console.log(path)
    let {data, fetchError} = ApiClient.get(path);

    let log = data && data.log;
    let error = fetchError || (data && data.error);

    return (
        <Layout>
            <div>
                <Breadcrumb>
                    <Breadcrumb.Item href="/">Home</Breadcrumb.Item>
                    <Breadcrumb.Item href={'/requests/'+ request}>{request}</Breadcrumb.Item>
                    <Breadcrumb.Item active>{run}</Breadcrumb.Item>
                    <Breadcrumb.Item active>Log</Breadcrumb.Item>
                </Breadcrumb>

                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {log &&
                    <textarea className={styles.logtext} disabled>{log}</textarea>
                }
            </div>
        </Layout>
    )
};
