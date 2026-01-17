import { Component } from '@angular/core';

export interface IUser {
    id: number;
    name: string;
}

export type UserID = number;

export enum UserRole {
    Admin,
    User
}

export abstract class BaseService {
    abstract getData(): void;
}

export class UserService extends BaseService {
    private users: IUser[] = [];

    constructor() {
        super();
    }

    public getData(): void { }
}

export function helper<T>(val: T): T {
    return val;
}

export const arrowHelper = (x: number) => x * 2;
