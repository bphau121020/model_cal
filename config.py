from firebase import firebase


def connection():
    fb = firebase.FirebaseApplication(
        "https://dta-cache-default-rtdb.firebaseio.com/", None
    )
    return fb
