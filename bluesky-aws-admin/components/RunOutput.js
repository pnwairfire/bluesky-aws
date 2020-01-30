import { ApiClient } from '../lib/apiutils'
import Alert from 'react-bootstrap/Alert'
//import ReactJson from 'react-json-view'

import LoadingSpinner from './LoadingSpinner';
import styles from './RunOutput.module.css'

export default function RequestInput(props) {

    if (props && props.request && props.run) {
        let path ='/api/requests/' + props.request + '/runs/' + props.run + '/output'
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
                    <textarea value={JSON.stringify(outputData, null, 4)} disabled />
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};
