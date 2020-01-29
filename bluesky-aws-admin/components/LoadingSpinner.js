import Spinner from 'react-bootstrap/Spinner'

import styles from './LoadingSpinner.module.css'

export default function LoadingSpinner(props) {
    return (
        <div className={styles['loading-spinner']}>
            <Spinner animation="border" role="status" size="sm">
            </Spinner>
            <span>Loading...</span>
        </div>
    )
}