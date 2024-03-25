package lambda_exp;


interface Add{
	int add();
	//int add(int a,int b);
}
public class LambdaExpression {
	public static void main(String[] args) {
		
		
		Add n1 = ()->20+20;
		System.out.println(n1.add());
		
//		Add n1 = (a,b)->a+b;
//		System.out.println(n1.add(10,20));
	}
}
