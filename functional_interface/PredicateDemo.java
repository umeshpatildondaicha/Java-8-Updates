package functional_interface;
import java.util.Arrays;
import java.util.List;

public class PredicateDemo {
	public static void main(String[] args) {
//		Check Number Even or Odd
		List<Integer> list = Arrays.asList(1,2,3,4,5,6,7,8,9,10,11);
		list.stream().filter(i -> (i&1)==0).forEach(i -> System.out.println("This is even : "+i));
	}
}