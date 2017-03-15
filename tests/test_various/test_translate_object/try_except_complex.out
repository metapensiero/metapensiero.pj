var value;
value = 0;
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
    value += 1;
    throw new MyError("Something bad happened");
    value += 1;
} catch(e) {
    if ((e instanceof MySecondError)) {
        value += 20;
    } else {
        if ((e instanceof MyError)) {
            value += 30;
        } else {
            value += 40;
        }
    }
} finally {
    value += 1;
}
