

import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.Spliterator;

public class IteratorPractice {
	public static void main(String[] args) {
		List<String> l= Arrays.asList("Hi","Hii","Hiii");
		
//		Iterator
		Iterator<String> i = l.iterator();
		while(i.hasNext()) {
			System.out.println(i.next());
		}
		
//		forEach
		l.forEach(System.out::println);
		
//		Spliterator
		Spliterator<String> s = l.spliterator();
		s.forEachRemaining(System.out::print);
	}
}
