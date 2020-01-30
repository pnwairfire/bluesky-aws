import Alert from 'react-bootstrap/Alert'

import LoadingSpinner from './LoadingSpinner';
import { ApiClient } from '../lib/apiutils'
import styles from './RunLog.module.css'

export default function RunLog(props) {
    if (props && props.request && props.run) {
        let path ='/api/requests/' + props.request + '/runs/' + props.run + '/log'
        let {data, fetchError} = ApiClient.get(path);

        let log = data && data.log;
        let error = fetchError || (data && data.error);

        return (
            <div>
                <h5>Run Log</h5>
                {!data &&
                    <LoadingSpinner />
                }
                {error &&
                    <Alert variant="danger">{error}</Alert>
                }
                {log &&
                    <textarea className={styles.logtext} value={log} disabled />
                }
            </div>
        )
    } else {
        // need to explicitly return null so that nothing is rendered
        return null
    }
};
