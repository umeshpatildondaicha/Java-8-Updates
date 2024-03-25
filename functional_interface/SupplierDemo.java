package functional_interface;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.function.Supplier;

public class SupplierDemo {
	public static void main(String[] args) {
		List<Integer> list = Arrays.asList(1,1,2,34,34);
		Supplier<List<Integer>> e = () -> new ArrayList<>(new HashSet<>(list));
		System.out.println(e.get());

	}
}
//Supplier<List<Integer>> d = ()->{
//	List<Integer> lst = new ArrayList<>();
//	for(int i : list) {
//		if (!lst.contains(i)) {
//            lst.add(i);
//        }
//	}
//	return lst;
//};