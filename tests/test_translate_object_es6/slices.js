function func() {
    var foo;
    foo = "foofoo";
    foo.slice(1);
    foo.slice(0, (- 1));
    foo.slice(3, (- 1));
    foo[2];
}
