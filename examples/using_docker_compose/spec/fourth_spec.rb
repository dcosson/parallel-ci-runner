require 'rspec'

RSpec.describe 'Fourth Spec' do
  it 'should pass' do
    sleep(4)
    expect(1+1).to eq(2)
  end
end
