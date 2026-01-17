import fs from 'fs';

export const CONST_VAR = 42;
let mutableVar = "string";

export class JSClass {
    constructor() {
        this.value = 1;
    }

    method() {
        return true;
    }
}

export function regularFunc(a, b) {
    return a + b;
}

export const arrowFunc = (x) => x * x;

export async function asyncFunc() {
    await Promise.resolve();
}

const internalArrow = () => { };
