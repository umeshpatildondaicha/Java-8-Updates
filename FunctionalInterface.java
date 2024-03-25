package Java8Updates;

import java.util.function.Consumer;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.function.Supplier;

public class FunctionalInterface {
	public static void main(String[] args) {
//		T - the type of the input to the function
//		R - the type of the result of the function
		
//		Function<T,R> -> RT - Specifies
		Function<Integer, Integer> a = (num) -> num*2;
		Function<Integer, Double> b = (num) -> (double) (num *num);
		System.out.println(a.apply(10));
		System.out.println(b.apply(10));
		
//		Predicate<T> -> Boolean
		Predicate<Integer> predicate = (num)->num>0;
		System.out.println(predicate.test(10));
		System.out.println(predicate.test(0));
		
//		Consumer<T> -> Void
		Consumer<Double> d = (n)-> System.out.println(n);
		Consumer<String> e = (n)-> System.out.println(n);
		d.accept(10.8);
		e.accept("HEllo Umesh");

//		Supplier<T> -> R - We Want
		Supplier<Double> r = () -> {
			Double integer = (double)(Math.random() * 100);
			//String.valueOf(integer);
	        return integer;
		};
		System.out.println(r.get());
		
		
	}
}
