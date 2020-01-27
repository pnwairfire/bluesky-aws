import { ApiClient } from '../lib/apiutils'
import Alert from 'react-bootstrap/Table'

import styles from './RunLog.module.css'

export default function RequestInput(props) {
    let path ='/api/requests/' + props.request + '/input'
    let {data, fetchError} = ApiClient.get(path);

    let inputData = data && data.input;
    let error = fetchError || (data && data.error);

    return (
        <div>
            {error &&
                <Alert variant="danger">{error}</Alert>
            }
            {inputData &&
                <textarea className={styles.requestinput} value={JSON.stringify(inputData)} disabled />
            }
        </div>
    )
};
