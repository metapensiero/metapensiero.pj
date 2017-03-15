function MyError(message) {
    this.name = "MyError";
    this.message = (message || "Custom error MyError");
    if (((typeof Error.captureStackTrace) === "function")) {
        Error.captureStackTrace(this, this.constructor);
    } else {
        this.stack = new Error(message).stack;
    }
}
MyError.prototype = Object.create(Error.prototype);
MyError.prototype.constructor = MyError;
class MySecondError extends MyError {
    /* A stupid error */
}
