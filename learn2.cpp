// learn2.cpp - pointers and references

#include<iostream>
using namespace std;

// Function that takes a copy- changes do NOT affect original
void addTenCopy(int n){
    n=n+10;
    cout<<"Inside addTenCopy:  "<<n<<endl;
}

//Function that takes a REFERENCE - changes DO affect original
void addTenRef (int &n){
    n=n+10;
    cout<<"Inside addTenCopy: "<<n<<endl;
}

//Function that takes a POINTER - changes DO affect original
void addTenPtr(int*n){
    *n=*n+10;
    cout<<"Inside addTenPtr: "<<*n<<endl;
}
int main(){

    //PART 1: address-of and dereference
    int x=42;
    int*ptr=&x;   //ptr stores the ADDRESS of x

    cout<<"Value of x:         "<<x<<endl;
    cout<<"Address of x(&x):   "<<&x<<endl;
    cout<<"Value of ptr:       "<<ptr<<endl;  //same as &x
    cout<<"Value at ptr(*ptr): "<<*ptr<<endl;  //same as x
    
    //Changing x through the pointer:
    *ptr=99;
    cout<<"After *ptr= 99 , x= "<<x<<endl;  //x is now 99!
    
    //PART 2: reference = alias
    int y =10;
    int &ref =y;     // ref ISy - same memory location

    cout<<"\ny= "<<y<<", ref= "<<ref<<endl;
    ref= 50;    // changing ref changes y
    cout<<"After ref = 50, y = "<<y<<endl;    // y is now 50!

    //PART 3: copy vs reference vs pointer in functions
    int a = 5;
    cout<<"\nBefore addTenCopy: a= "<<a<<endl;
    addTenCopy(a);
    cout<<"After addTenCopy: a= "<<a<< endl; //still 5!

    int b= 5;
    cout<<"\nBefore addTenRef: b= "<<b<<endl;
    addTenRef(b);
    cout<<"After addTenRef: b= "<<b<<endl; //now 15!

    int c= 5;
    cout<<"\nBefore addTenPtr: c= "<<c<<endl;
    addTenPtr(&c);
    cout<<"After addTenPtr: c= "<<c<<endl; //now 15!
    
    return 0;
}