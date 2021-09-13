import axios from 'axios';


export class NodeAPI {
    GetPort() {
        return new Promise((resolve, reject) => {
            axios.get(`${localStorage.getItem("node")}/port`)
                .then(response => resolve(response.data))
                .catch(error => reject(error))
        });
    }

    GetChain() {
        return new Promise((resolve, reject) => {
            axios.get(`${localStorage.getItem("node")}/chain`)
                .then(response => resolve(response.data))
                .catch(error => reject(error))
        });
    }

    Mine() {
        return new Promise((resolve, reject) => {
            axios.get(`${localStorage.getItem("node")}/mine`)
                .then(response => resolve(response.data))
                .catch(error => reject(error))
        });
    }

    ResolveConflicts() {
        return new Promise((resolve, reject) => {
            axios.get(`${localStorage.getItem("node")}/nodes/resolve`)
                .then(response => resolve(response.data))
                .catch(error => reject(error))
        });
    }

    FulfillContract(id) {
        return new Promise((resolve, reject) => {
            axios.post(`${localStorage.getItem("node")}/contract/${id}/export_oracle`)
                .then(response => resolve(response.data))
                .catch(error => reject(error))
        });
    }
}

export const nodeAPI = new NodeAPI();
