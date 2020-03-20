import Calendar from 'react-calendar';
import Modal from 'react-bootstrap/Modal'
import { useState } from 'react';
import { FaRegCalendarAlt } from "react-icons/fa";

import ButtonWithToolTip from './ButtonWithToolTip'

export default function CalendarModal(props) {
    const [show, setShow] = useState(false);

    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);
    const onChange = (date) => {
        props.handleMonthChange(date)
        setShow(false);
    }

    return (
        <>
            <ButtonWithToolTip
                title="Select A Different Month"
                onClick={handleShow}
                disabled={false}>
                <FaRegCalendarAlt />
            </ButtonWithToolTip>
            <Modal show={show} onHide={handleClose}
                    animation={false} centered>
                <Modal.Header closeButton>
                    <Modal.Title id="contained-modal-title-vcenter">
                        Select a Month
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Calendar
                        defaultView="year"
                        onChange={onChange}
                        value={props.month}
                        maxDetail="year"
                        minDetail="year"
                    />
                </Modal.Body>
            </Modal>
        </>
    );
}