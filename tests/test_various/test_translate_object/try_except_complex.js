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
function MyThirdError(message) {
    this.name = "MyThirdError";
    this.message = (message || "Custom error MyThirdError");
    if (((typeof Error.captureStackTrace) === "function")) {
        Error.captureStackTrace(this, this.constructor);
    } else {
        this.stack = new Error(message).stack;
    }
}
MyThirdError.prototype = Object.create(Error.prototype);
MyThirdError.prototype.constructor = MyThirdError;
function MyFourthError(message) {
    this.name = "MyFourthError";
    this.message = (message || "Custom error MyFourthError");
    if (((typeof Error.captureStackTrace) === "function")) {
        Error.captureStackTrace(this, this.constructor);
    } else {
        this.stack = new Error(message).stack;
    }
}
MyFourthError.prototype = Object.create(Error.prototype);
MyFourthError.prototype.constructor = MyFourthError;
try {
    value += 1;
    throw new MyError("Something bad happened");
    value += 1;
} catch(e) {
    if ((e instanceof MySecondError)) {
        let err = e;
        value += 20;
    } else {
        if (((e instanceof MyThirdError) || (e instanceof MyFourthError))) {
            let err2 = e;
            value += 30;
        } else {
            if ((e instanceof MyError)) {
                value += 40;
            } else {
                value += 50;
            }
        }
    }
} finally {
    value += 1;
}
