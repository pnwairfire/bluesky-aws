import Alert from 'react-bootstrap/Alert'
import dynamic from 'next/dynamic';
const ReactJson=dynamic(import ('react-json-view'),{ssr:false});

import LoadingSpinner from './LoadingSpinner';
import { ApiClient } from '../lib/apiutils'
import styles from './RunInput.module.css'

export default function RunInput(props) {
    if (props && props.request && props.run) {
        let path ='/api/requests/' + encodeURIComponent(props.request)
        + '/runs/' + encodeURIComponent(props.run) + '/input'
        let {data, fetchError} = ApiClient.get(path);

        let inputData = data && data.input;
        let error = fetchError || (data && data.error);

        return (
            <div className={styles['input-viewer']}>
                <h5>Run Input</h5>
                {!data &&
                    <LoadingSpinner />
                }
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {inputData &&
                    <div className={styles['json-viewer']}>
                        <ReactJson src={inputData} theme="monokai" />
                    </div>
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};
