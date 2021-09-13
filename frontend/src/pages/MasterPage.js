import {Avatar, Button, Col, List, Row, Table, Typography} from "antd";
import React, {useEffect, useState} from "react";
import history from '../history';
import {masterAPI} from "../http/MasterAPI";

const {Title} = Typography;

const columns = [
    {
        title: 'Порт отправления',
        dataIndex: 'port_from',
        key: 'port_from',
    },
    {
        title: 'Порт прибытия',
        dataIndex: 'port_to',
        key: 'port_to',
    },
    {
        title: 'Стоимость',
        dataIndex: 'cost',
        key: 'cost',
    },
];

const MasterPage = () => {
    const [nodes, setNodes] = useState([]);
    const [contracts, setContracts] = useState([]);

    useEffect(() => {
        masterAPI.GetNodes().then((res) => setNodes(res));
        masterAPI.GetContracts().then((res) => setContracts(res.reverse()));
    }, []);

    return <>
        <Row justify="center" align="middle">
            <Col xs={{span: 22}} md={{span: 18}} lg={{span: 14}}>
                <Row align="middle" justify="center" gutter={16} style={{marginTop: "40px"}}>
                    <Col>
                        <Title level={1}>SmartChain</Title>
                    </Col>
                </Row>
                <Row justify="center">
                    <Col xl={12} lg={12} md={18} sm={20} xs={22}>
                        <Title level={3}>Цифровые порты</Title>
                        <List
                            itemLayout="horizontal"
                            dataSource={nodes}
                            renderItem={item => (
                                <List.Item>
                                    <List.Item.Meta
                                        avatar={<Avatar src="https://cdn-icons-png.flaticon.com/512/995/995286.png"/>}
                                        title={<a onClick={() => {
                                            localStorage.setItem("node", item.address);
                                            history.push(`/node/${item.id}`);
                                        }}>{item.name} ({item.id})</a>}
                                        description={item.address}
                                    />
                                </List.Item>
                            )}
                        />
                        <Button disabled>Добавить</Button>
                    </Col>
                    <Col xl={12} lg={12} md={18} sm={20} xs={22}>
                        <Title level={3}>Последние контракты</Title>
                        <Table dataSource={contracts} columns={columns}/>
                    </Col>
                </Row>
            </Col>
        </Row>
    </>
}

export default MasterPage;
