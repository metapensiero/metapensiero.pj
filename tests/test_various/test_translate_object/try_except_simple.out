var value;
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
try {
    value = 0;
    throw new MySecondError("This is an error");
} catch(e) {
    if ((e instanceof MySecondError)) {
        value = 1;
    } else {
        throw e;
    }
}
