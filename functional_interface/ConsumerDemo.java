package functional_interface;

import java.util.Arrays;
import java.util.List;

public class ConsumerDemo {
	public static void main(String[] args) {
		List<Integer> list = Arrays.asList(1,2,3,4,5,6,7,8,9,10,11);
		list.stream().forEach(i -> System.out.println("This is : "+i));
	}
}
