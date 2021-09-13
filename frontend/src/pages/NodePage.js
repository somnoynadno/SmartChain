import React, {useEffect, useState} from 'react';
import {Button, Col, Input, message, Modal, PageHeader, Row, Select, Table, Tag, Typography} from "antd";
import history from "../history";
import {nodeAPI} from "../http/NodeAPI";
import {masterAPI} from "../http/MasterAPI";

const {Title} = Typography;
const {Option} = Select;

const NodePage = () => {
    const [isModalVisible, setIsModalVisible] = useState(false);

    const [isHelpModalVisible, setIsHelpModalVisible] = useState(!localStorage.getItem("help_shown"));

    const handleHelpOk = () => {
        localStorage.setItem("help_shown", "true");
        setIsHelpModalVisible(false);
    };

    const [port, setPort] = useState(null);
    const [portToID, setPortToID] = useState("");
    const [portFromID, setPortFromID] = useState("");
    const [cost, setCost] = useState(0);
    const [contracts, setContracts] = useState([]);
    const [ports, setPorts] = useState([]);

    useEffect(() => {
        getPort();
        getPorts();
        getContracts();
    }, []);

    const getPort = () => {
        nodeAPI.GetPort().then((res) => {
            setPort(res);
            setPortFromID(res.id);
        }).catch((err) => message.error("Не удалось получить данные для порта"));
    }

    const getPorts = () => {
        masterAPI.GetNodes().then((res) => {
            setPorts(res);
        }).catch((err) => message.error("Не удалось получить список портов"));
    }

    const getContracts = () => {
        nodeAPI.GetChain().then((res) => {
            let newContracts = [];
            for (let block of res['chain'].reverse()) {
                for (let c of block['transactions']) {
                    newContracts.push(c);
                }
            }

            setContracts(newContracts);
            message.info("Получен список контрактов");
        });
    }

    const createContract = () => {
        let contract = {
            "port_from": portFromID,
            "port_to": portToID,
            "cost": parseInt(cost),
        }
        masterAPI.CreateContract(contract)
            .then((res) => message.success("Контракт успешно добавлен в текущий блок"))
            .catch((err) => message.error(err.toString()));
    }

    const mine = () => {
        nodeAPI.Mine().then((res) => message.info("Создан новый блок"));
        getContracts();
        getPort();
    }

    const resolve = () => {
        nodeAPI.ResolveConflicts().then((res) => message.info("Конфликты решены"));
        getContracts();
        getPort();
    }

    const columns = [
        {
            title: 'Порт отправления',
            dataIndex: 'from_address',
            key: 'from_address',
        },
        {
            title: 'Порт прибытия',
            dataIndex: 'to_address',
            key: 'to_address',
        },
        {
            title: 'Стоимость',
            dataIndex: 'cost',
            key: 'cost',
        },
        {
            title: 'Статус',
            key: 'is_done',
            dataIndex: 'is_done',
            render: (text, record) => (
                <Tag color={record["is_done"] ? "green" : "blue"}>{record["is_done"] ? "Выполнен" : "Создан"}</Tag>
            ),
        },
        {
            title: 'Действие',
            key: 'action',
            dataIndex: 'action',
            render: (text, record) => (
                record["to_address"] === portFromID && !record["is_done"] &&
                <Button onClick={() => {
                    nodeAPI.FulfillContract(record["uuid"]).then((res) => message.success("Контракт исполнен"));
                }}>Исполнить</Button>
            ),
        }
    ];

    const showModal = () => {
        setIsModalVisible(true);
    };

    const handleOk = () => {
        setIsModalVisible(false);
        createContract();
    };

    const handleCancel = () => {
        setIsModalVisible(false);
    };

    return <>
        <Modal title="Небольшая инструкция по майнингу" visible={isHelpModalVisible} onOk={handleHelpOk}
               onCancel={handleHelpOk}>
            <p><b>Это модальное окно отображается только один раз.</b></p>
            <p>Между цифровыми портами можно создавать смарт-контракты.
                Созданный контракт будет получен каждым портом и добавлен в последний блок их блокчейна.
                Чтобы полученный контракт сохранился в истории, нужно <b>намайнить блок</b> со всеми текущими
                контрактами,
                а также <b>разрешить все существующие конфликты</b> между узлами блокчейна, тем самым опубликовав
                созданный
                блок или приняв самую длинную найденную цепочку за основную. <i>Функциональные кнопки для этого
                    расположены
                    в левом нижнем углу.</i>
            </p>
            <p>Созданный контракт может быть <b>исполнен</b> (подтвержден) портом получателем. Для этого нужно вернуться
                назад,
                открыть вкладку данного порта, снова намайнить блок и/или решить конфликты узлов.</p>
            <p>После майнинга следующего блока смарт-контракты будут <b>автоматически выполнены</b>: изменится баланс
                порта-отправителя и порта-получателя груза. <i>Баланс может уйти в минус: в рамках MVP все данные
                    проверки не предусмотрены.</i></p>
        </Modal>
        <Modal title="Создать контракт" visible={isModalVisible} onOk={handleOk} onCancel={handleCancel}>
            Порт отправления
            <Input onChange={(event) => {
            }} value={`${portFromID}`} disabled/>
            <br/><br/>
            Порт прибытия
            <br/>
            <Select style={{width: "100%"}} onChange={(value) => setPortToID(value)}>
                {ports.map((p, i) => {
                    if (p.id !== portFromID) return <Option key={i} value={p.id}>{p.name} ({p.id})</Option>
                    else return '';
                })}
            </Select>
            <br/><br/>
            Стоимость
            <Input type={"number"} onChange={(event) => {
                setCost(event.target.value)
            }} placeholder={'100'}/>
            <br/><br/>
            Дополнительно
            <Input disabled/>
        </Modal>
        <Row justify="center" align="middle">
            <Col xs={{span: 22}} md={{span: 20}} lg={{span: 16}}>
                <Row gutter={16} style={{marginTop: "40px"}}>
                    <Col>
                        <PageHeader
                            className="site-page-header"
                            onBack={() => history.push('/')}
                            title={<Title level={2}>Порт {portFromID}</Title>}
                            subTitle={localStorage.getItem("node")}
                        />
                    </Col>
                </Row>
                <Row justify="center">
                    <Col xl={11} lg={11} md={18} sm={20} xs={22}>
                        <iframe src={`https://www.vesselfinder.com/ru/ports/${portFromID}`}
                                title="Port" width="100%" height="500"/>
                        <Button onClick={() => mine()}>Намайнить блок</Button>
                        <Button onClick={() => resolve()}>Решить конфликты</Button>
                    </Col>
                    <Col xl={1} lg={1} md={0} sm={0} xs={0}/>
                    <Col xl={11} lg={11} md={18} sm={20} xs={22}>
                        <Title level={3}>Контракты</Title>
                        <Button onClick={showModal}>Создать новый</Button>
                        <span style={{marginLeft: 5}}>Баланс: {port ? port.balance : "..."}</span>
                        <Table dataSource={contracts} columns={columns}/>
                    </Col>
                </Row>
            </Col>
        </Row>
    </>
}

export default NodePage;
