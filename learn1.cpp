//learn1.cpp - C++ vairables and types
//Type every character. Do not copy-paste.


#include<iostream>
#include<string>
using namespace std;
int main(){
    //INTEGER-whole numbers only
    int age=19;
    int year=2025;
    int sum=age+year;
    cout<<"Age: "<<age<<endl;
    cout<<"Year: "<<year<<endl;
    cout<<"Sum: "<<sum<<endl;

    //DOUBLE - decimal numbers
    double pi=3.14159;
    float gpa= 9.2f;
    cout<<"Pi: "<<pi<<endl;
    cout<<"GPA: "<<gpa<<endl;

    //BOOL -only true or false(prints as 1 or 0 in C++)
    bool isStudent= true;
    bool ISGraduated= false;
    cout<<"Is student: "<<isStudent<<endl;  //prints 1
    cout<<"Is gradauted: "<<ISGraduated<<endl;  //prints 0

    //STRING - TEXT (needs # include <string> at top)
    string name= "Chitraksh";
    string project= "GROK";
    cout<<"Name: "<<name<<endl;
    cout<<"Bluiding: "<<project<<endl;

    //CHAR- single character (uses single quotes, not double)
    char grade ='A';
    cout<<"Target grade: "<< grade <<endl;

    //INTEGER DIVISION TRAP - write thsi in notebook:
    int a = 7;
    int b= 2;
    cout<<"7/2 as int: "<<a/b<<endl;  //print 3, not 3.5!
    cout<<"7/2 as double: "<<a/(double)b<<endl; //prints 3.5

    return 0;

}