class A {
    async method() {
    }
}
class B extends A {
    async method() {
        await A.prototype.method.call(this);
    }
}
