import Alert from 'react-bootstrap/Alert'

import styles from './RequestStatus.module.css'


export default function RequestStatus(props) {
    return (
        <div className={styles['request-status']}>
            {props && props.status && (
                <div>
                    <div className={styles['page-section']}>
                        <div><b>Request</b>: {props.request}</div>
                        <div><b>System</b>: {props.status.system_state}</div>
                        {props.status.system_error && (
                            <Alert variant="danger">{props.status.system_error}</Alert>
                        )}
                        <div><b>Message</b>: {props.status.system_message || '(none)'}</div>
                    </div>
                </div>
            ) || (
                <Alert variant="warning">
                    (no request status information)
                </Alert>
            )}
        </div>
    )
}
