import Alert from 'react-bootstrap/Alert'
import dynamic from 'next/dynamic';
const ReactJson=dynamic(import ('react-json-view'),{ssr:false});

import { ApiClient } from '../lib/apiutils'
import LoadingSpinner from './LoadingSpinner';
import styles from './RunOutput.module.css'

export default function RequestInput(props) {

    if (props && props.request && props.run) {
        let path ='/api/requests/' + encodeURIComponent(props.request)
            + '/runs/' + encodeURIComponent(props.run) + '/output'
        let {data, fetchError} = ApiClient.get(path);

        let outputData = data && data.output;
        let error = fetchError || (data && data.error);

        return (
            <div className={styles['run-output']}>
                <h5>Run output</h5>
                {!data &&
                    <LoadingSpinner />
                }
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {outputData &&
                    <div className={styles['json-viewer']}>
                        <ReactJson src={outputData} theme="monokai" />
                    </div>
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};
