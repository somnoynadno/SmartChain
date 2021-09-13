import axios from 'axios';
import {masterAddress} from "../config";


export class MasterAPI {
    GetNodes() {
        return new Promise((resolve, reject) => {
            axios.get(`${masterAddress}/get_nodes`)
                .then(response => resolve(response.data))
                .catch(error => reject(error))
        });
    }

    GetContracts() {
        return new Promise((resolve, reject) => {
            axios.get(`${masterAddress}/get_contracts`)
                .then(response => resolve(response.data))
                .catch(error => reject(error))
        });
    }

    CreateContract(contract) {
        return new Promise((resolve, reject) => {
            axios.post(`${masterAddress}/create_contract`, contract)
                .then(response => resolve(response.data))
                .catch(error => reject(error))
        });
    }
}

export const masterAPI = new MasterAPI();
