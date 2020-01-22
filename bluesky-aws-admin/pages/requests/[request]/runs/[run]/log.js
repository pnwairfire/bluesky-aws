import { useRouter } from 'next/router'
import Alert from 'react-bootstrap/Table'

import Layout from '../../../../../components/Layout'
import { getRunLog } from '../../../../../lib/status'
import { ApiClient } from '../../../../../lib/apiutils'


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
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {log &&

                    {log}

                }
            </div>
        </Layout>
    )
};
